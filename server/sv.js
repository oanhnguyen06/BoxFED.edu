import express from "express";
import cors from "cors";
import { Ollama } from "ollama";

const app = express();
app.use(cors());
app.use(express.json());

const client = new Ollama();

app.post("/chat", async (req, res) => {
    try {
        const { message } = req.body;
        const reply = await client.generate({
            model: "llama3.2",
            prompt: message
        });

        res.json({ reply: reply.response });
    } catch (err) {
        res.status(500).json({ reply: "Lỗi server!" });
    }
});

app.listen(3000, () => console.log("Chatbot server chạy tại http://localhost:3000"));
