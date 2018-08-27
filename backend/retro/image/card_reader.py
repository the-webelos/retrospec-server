import numpy as np
import cv2 as cv
import boto3


class CardReader(object):
    CARD_COLOR_BITS = 2

    def __init__(self, image_bytes: bytes):
        self.image = self._image_from_bytes(image_bytes)

    def get_cards_content(self):
        card_squares = self._get_card_squares()
        text_blocks = self._get_text_blocks()

        bundles = self._bundle_words(card_squares, text_blocks)
        self._populate_bundle_colors(bundles)

        # turn bundles into cards
        contents = []
        for bundle in bundles:
            contents.append({'text': ' '.join(bundle['words']),
                             'color': CardReader._get_hex_from_bundle_colors(bundle['color'][:3]),
                             'confidence': bundle['confidence']})

        return contents

    @staticmethod
    def _is_text_block_in_contour(points, contour):
        for point in points:
            if cv.pointPolygonTest(contour, (point[0], point[1]), False) < 0:
                return False

        return True

    def _bundle_words(self, card_squares, text_blocks):
        bundles = []
        matched = set()

        # collect all the words found in a post-it
        #  iterate over all the post it bounding boxes and collect all the text squares that are inside a single box.
        #  once a text box is matched to a post it, don't try to match it again
        for square in card_squares:
            words = []
            confidence = 100.0
            word_boxes = []
            for x, text in enumerate(text_blocks):
                if x in matched:
                    continue
                if self._is_text_block_in_contour(text['points'], square):
                    words.append(text['text'])
                    word_boxes.append(np.array(text['points'], dtype=np.int32))
                    confidence = min(confidence, text['confidence'])
                    matched.add(x)
            if words:
                bundles.append({'words': words, 'word_boxes': word_boxes, 'confidence': confidence, 'contour': square})

        return bundles

    def _populate_bundle_colors(self, bundles):
        mask_bit = 0xFF
        mask_bit = mask_bit << (8 - self.CARD_COLOR_BITS)

        mask = np.zeros(self.image.shape[:2], np.uint8)
        # get the average color in a post it.
        for bundle in bundles:
            mask[...] = 0
            cv.drawContours(mask, [bundle['contour']], -1, 255, -1)
            cv.drawContours(mask, bundle['word_boxes'], -1, 0, -1)

            color = cv.mean(self.image, mask=mask)
            # use the mask bit to limit number of colors we record
            bundle['color'] = [int(c) & mask_bit for c in color]

    @staticmethod
    def _get_hex_from_bundle_colors(colors):
        return "#{:02x}{:02x}{:02x}".format(colors[0], colors[1], colors[2])

    @staticmethod
    def _get_points_from_geometry(poly_points, shape):
        points = []
        for p in poly_points:
            points.append([int(p['X'] * shape[1]), int(p['Y'] * shape[0])])
        return points

    def _get_text_blocks(self):
        rekognition = boto3.client("rekognition", region_name='us-east-1')

        gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        denoise = cv.fastNlMeansDenoising(gray)
        blur = cv.medianBlur(denoise, 7)

        gray_bytes = cv.imencode('.png', blur)[1].tostring()

        response = rekognition.detect_text(Image={'Bytes': gray_bytes})

        blocks = []
        for detection in response['TextDetections']:
            if detection['Type'] == 'WORD':
                # turn the points into cv pixel counts
                points = self._get_points_from_geometry(detection['Geometry']['Polygon'], self.image.shape)
                blocks.append({'points': points,
                               'text': detection['DetectedText'],
                               'confidence': detection['Confidence']})

        return blocks

    @staticmethod
    def _angle_cos(p0, p1, p2):
        d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
        return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1)*np.dot(d2, d2)))

    def _get_card_squares(self):
        img_h, img_w = self.image.shape[:2]
        img_area_thrs = img_h * img_w * .95

        gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        denoise = cv.fastNlMeansDenoising(gray)
        blur = cv.GaussianBlur(denoise, (5, 5), 0)

        squares = []
        for thrs in range(1, 255, 6):
            dst = cv.threshold(blur, thrs, 255, cv.THRESH_BINARY)[1]
            contours = cv.findContours(dst, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)[1]

            for cnt in contours:
                cnt_len = cv.arcLength(cnt, True)
                cnt = cv.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4:
                    cnt_area = cv.contourArea(cnt)
                    if 1000 < cnt_area < img_area_thrs and cv.isContourConvex(cnt):
                        cnt = cnt.reshape(-1, 2)
                        max_cos = np.max([self._angle_cos(cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4]) for i in range(4)])
                        if max_cos < 0.05:
                            squares.append(cnt)
        return squares

    @staticmethod
    def _image_from_bytes(img_bytes):
        nparr = np.frombuffer(img_bytes, np.uint8)
        return cv.imdecode(nparr, cv.IMREAD_COLOR)


if __name__ == '__main__':
    import sys
    from pprint import pprint

    with open(sys.argv[1], 'rb') as f:
        card_reader = CardReader(f.read())

    cards = card_reader.get_cards_content()

    pprint(cards)
