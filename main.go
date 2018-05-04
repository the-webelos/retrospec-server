package main

import (
	"log"
	"net/http"

	"github.com/gorilla/websocket"
	"github.com/joho/godotenv"
)

// User is the struct defining a user's details
type User struct {
	Name  string `json:"name"`
	Email string `json:"email"`
}

// Message describes the message payload
type Message struct {
	User    User   `json:"user"`
	Message string `json:"message"`
	Column  string `json:"column"`
}

var clients = make(map[*websocket.Conn]bool)
var broadcast = make(chan Message)
var upgrader = websocket.Upgrader{}

func main() {
	envErr := godotenv.Load()
	if envErr != nil {
		log.Fatal("Error loading .env file")
	}

	fs := http.FileServer(http.Dir("./public"))

	http.Handle("/", fs)
	http.HandleFunc("/ws", handleConnections)

	go handleMessages()

	log.Println("http server started on :8000")
	err := http.ListenAndServe(":8000", nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}

func handleConnections(w http.ResponseWriter, r *http.Request) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Fatal(err)
	}

	defer ws.Close()

	clients[ws] = true

	for {
		var msg Message
		err := ws.ReadJSON(&msg)
		if err != nil {
			delete(clients, ws)
			break
		}
		broadcast <- msg
	}
}

func handleMessages() {
	for {
		msg := <-broadcast
		for client := range clients {
			err := client.WriteJSON(msg)
			if err != nil {
				client.Close()
				delete(clients, client)
			}
		}
	}
}
