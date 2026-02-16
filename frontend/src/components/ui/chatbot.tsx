import { Box, Button, Flex, Heading, HStack, Input, Text, VStack } from "@chakra-ui/react";
import { fileUploadService } from "@/client"
import { useState } from "react";
import { Message } from "@/client/types.gen";
import { FaPaperPlane, FaRobot } from "react-icons/fa"

interface chatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
}

export default function Chatbot() {

    const [message, setMessage] = useState<string>("")
    const [messages, setMessages] = useState<chatMessage[]>([])

    const handleSendMessage = async () => {
        if (!message.trim()) return
        const newMessage: chatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: message,
            timestamp: new Date().toISOString(),
        }
        setMessages((prev) => [...prev, newMessage])
        const userInput: Message = { message }

        try {
            const res = await fileUploadService.chatWithDocument(userInput)

            const assistantMessage: chatMessage = {
                id: Date.now().toString(),
                role: 'assistant',
                content: res.message,
                timestamp: new Date().toISOString(),
            }
            setMessages((prev) => [...prev, assistantMessage])
            setMessage("")
        } catch (error) {
            console.error("Error chatting with document:", error)
        }
        
    }

    const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            handleSendMessage()
        }
    }

    return (
        <Flex direction="column" h="100%" overflow="hidden" >
            <VStack align="stretch" flex="1" overflowY="auto" p={4} gap={6}>
                <Heading as="h2" size="xl" mb={2}>
                    AI Chatbot
                </Heading>
                {messages.map((msg) => (
                    <HStack maxW="100%" align="start" key={msg.id} justifyContent={msg.role === 'user' ? 'flex-end' : 'flex-start'} mb={2}>
                        {msg.role === 'assistant' && (
                            <Box
                                bg="blue.500"
                                color="white"
                                boxSize="32px"
                                rounded="full"
                                display="flex"
                                alignItems="center"
                                justifyContent="center"
                                mt={1}
                            >
                                <FaRobot />
                            </Box>
                        )}
                        <Box
                            bg={msg.role === 'user' ? "blue.600" : "white"}
                            color={msg.role === 'user' ? "white" : "gray.800"}
                            p={4}
                            rounded="2xl"
                            roundedTopLeft={msg.role === 'assistant' ? "2px" : "2xl"}
                            roundedTopRight={msg.role === 'user' ? "2px" : "2xl"}
                            shadow="sm"
                            border="1px solid"
                            borderColor={msg.role === 'assistant' ? "gray.200" : "transparent"}
                        >
                            <Text fontSize="sm" textAlign="left" >{msg.content}</Text>
                        </Box>
                    </HStack>
                ))}
            </VStack>


            <Box borderTop="1px solid" p={4}>
                <HStack px={4} py={2}>
                    <Button
                        aria-label="Add attachment"
                        size="sm"
                        variant="ghost"
                        color="gray.400"
                        rounded="full"
                        p={2}
                        minW="32px"
                    >
                        <span style={{ fontSize: '20px' }}>+</span>
                    </Button>

                    <Input
                        placeholder="Ask a question about your document..."
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        size="lg"
                        mb={4}
                        onKeyDown={handleKeyDown}
                    />
                    <Button
                        aria-label="Send message"
                        size="sm"
                        colorScheme="blue"
                        rounded="full"
                        onClick={handleSendMessage}
                        minW="32px"
                        p={2}
                    >
                        <FaPaperPlane />
                    </Button>
                </HStack>
            </Box>
    
        </Flex>
    )
}