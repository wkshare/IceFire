package main

import (
    "os"
    "os/exec"
)

func main() {
    cmd := exec.Command("ls", "/tmp")
    cmd.Start()
}
