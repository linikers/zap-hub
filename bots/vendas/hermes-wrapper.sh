#!/usr/bin/env bash
# Wrapper para o bridge de vendas - injeta personalidade vendas
# Este script substitui o hermes bin para o bot de vendas
exec /usr/local/bin/hermes chat --personality vendas -q "$1" --yolo
