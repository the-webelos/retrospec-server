# FunnerRetro Server

[![Build Status](https://travis-ci.org/carbonblack/funnerretro-server.svg?branch=master)](https://travis-ci.org/carbonblack/funnerretro-server)

This is the repo for the websocket server and user auth on FunnerRetro.

## Contributing

1. Install Go and Go Dep
2. `cd $GOPATH/src/`
3. `go get github.com/carbonblack/funnerretro-server`
4. Create a `.env` file in the root of this project and add `SIGNING_SECRET` and `PORT` to it
    * `SIGNING_SECRET=<some signing secret>`
    * `PORT=<some port>`
5. `dep ensure`
