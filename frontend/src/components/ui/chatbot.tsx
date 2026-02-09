import { Box, Heading, Input } from "@chakra-ui/react";
import { fileUploadService } from "@/client"
import { useState } from "react";
import { Message } from "@/client/types.gen";


export default function Chatbot() {
    const [response, setResponse] = useState<string>("")
    const [message, setMessage] = useState<string>("")

    const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            try {
                const userInput: Message = { message }
                const res = await fileUploadService.chatWithDocument(userInput)
                setResponse(res.message)
            } catch (error) {
                console.error("Error chatting with document:", error)
            }
        }
    }
    return (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%" }}>
            <Box textAlign="center" py={10} px={6}>
                <Heading as="h2" size="xl" mb={2}>
                    AI Chatbot
                </Heading>
                <Input
                    placeholder="Ask a question about your document..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    size="lg"
                    mb={4}
                    onKeyDown={handleKeyDown}
                />
                {response}
                
            </Box>
        </div>
    )
}