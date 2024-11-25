"use client";

import { Turn } from "./chat";
import { fetchCachedImage } from "./images";

export interface Message {
    name: string;
    image?: string;
    text: string;
}

export interface Action {
    name: string;
    arguments: string;
}

export interface Assistant {
    state: "start" | "stream" | "complete" | "full";
    payload?: string;
}

export interface Context {
    type: "action" | "user" | "issue" | "article";
    payload: string;
}

export interface SocketMessage {
    type: "action" | "assistant" | "context";
    payload: Action | Assistant | Context;
}


export class SocketServer {
    endpoint: string;
    socket: WebSocket | null;
    ready: boolean = false;
    threadId: string;
    callbacks: { [key: string]: (data: SocketMessage) => void } = {};
    onOpenCallback: () => void;
    onCloseCallback: () => void;


    constructor(endpoint: string, threadId: string, onOpenCallback: () => void, onCloseCallback: () => void) {
        this.endpoint = endpoint;
        this.threadId = threadId;
        this.socket = new WebSocket(endpoint);
        this.socket.onopen = this.onOpen;
        this.socket.onclose = this.onClose;
        this.socket.onmessage = this.onMessage;
        this.onOpenCallback = onOpenCallback;
        this.onCloseCallback = onCloseCallback;
    }

    addListener = (event: string, callback: (data: SocketMessage) => void) => {
        this.callbacks[event] = callback;
    }

    public send = (message: string) => {
        this.socket?.send(message);
    }

    public sendTurn = async (turn: Turn) => {
        const message: Message = {
            name: turn.name,
            text: turn.message
        };

        if (turn.image) {
            await fetchCachedImage(turn.image, (img) => {
                message.image = img;
                this.send(JSON.stringify(message))
            });
        } else {
            this.send(JSON.stringify(message));
        }
    };

    private onOpen = () => {
        this.ready = true;
        this.send(JSON.stringify({ threadId: this.threadId }));
        this.onOpenCallback();
        console.log("SocketServer: Connected to server");
    }

    private onClose = () => {
        this.ready = false;
        this.onCloseCallback();
        console.log("SocketServer: Disconnected from server");
    }

    private onMessage = (event: MessageEvent) => {
        try {
            const data = JSON.parse(event.data) as SocketMessage;
            //console.log("SocketServer: Received message", data);
            for (const key in this.callbacks) {
                this.callbacks[key](data);
            }
        } catch {
            console.error("SocketServer: Error parsing message", event.data);
        }
    }

    public close = () => {
        this.socket?.close();
        this.ready = false;
    }
}