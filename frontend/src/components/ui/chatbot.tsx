import { Box, Button, Flex, HStack, Input, VStack } from "@chakra-ui/react";
import { fileUploadService } from "@/client"
import { useState, useEffect} from "react";
import { Message, ChatMessage } from "@/client/types.gen";
import { FaPaperPlane, FaRobot } from "react-icons/fa"
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";


interface ChatMessageProps {
    itemId: string
}


export default function Chatbot({ itemId }: ChatMessageProps) {

    const [message, setMessage] = useState<string>("")
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [isLoading, setIsLoading] = useState<boolean>(false)

    useEffect(() => {
        const fetchChatLogs = async () => {
          try {
            const response = await fileUploadService.getChatLogs(itemId)
            setMessages(response.data)
          } catch (error) {
            console.error("Error fetching chat logs:", error)
          }
        }
        fetchChatLogs()
    }, [itemId])

    const handleSendMessage = async () => {
        if (!message.trim() || isLoading) return
        const newMessage: ChatMessage = {
            role: 'user',
            message: message,
            created_at: new Date().toISOString(),
        }
        setMessages((prev) => [...prev, newMessage])
        const userInput: Message = { message }
        setIsLoading(true)
        setMessage("")

        try {
            const res = await fileUploadService.chatWithDocument(userInput, itemId)

            const assistantMessage: ChatMessage = {
                role: 'assistant',
                message: res.message,
                created_at: new Date().toISOString(),
            }
            setMessages((prev) => [...prev, assistantMessage])
        } catch (error) {
            console.error("Error chatting with document:", error)
        } finally {
            setIsLoading(false)
        }
        
    }

    const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            handleSendMessage()
        }
    }

    return (
        <Flex direction="column" h="100%" overflow="hidden" bg="bg.panel">
            <VStack align="stretch" flex="1" overflowY="auto" p={4} gap={4}>
                {messages.map((msg, index) => (
                    <HStack key={index} maxW="100%" align="start"  justifyContent={msg.role === 'user' ? 'flex-end' : 'flex-start'} mb={2}>
                        {msg.role === 'assistant' && (
                            <Box
                                bg="blue.500"
                                color="white"
                                boxSize="32px"
                                minW="32px"
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
                            bg={msg.role === 'user' ? "bg" : "bg.muted"}
                            color={msg.role === 'user' ? "fg." : "fg"}
                            p={4}
                            rounded="2xl"
                            roundedTopLeft={msg.role === 'assistant' ? "2px" : "2xl"}
                            roundedTopRight={msg.role === 'user' ? "2px" : "2xl"}
                            shadow="none"
                            border="1px solid"
                            borderColor="border"
                        >
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm, remarkMath]}
                                rehypePlugins={[rehypeKatex]}
                            >
                                {msg.message}
                            </ReactMarkdown>
                        </Box>
                    </HStack>
                ))}
                {isLoading && (
                    <HStack maxW="100%" align="start" justifyContent="flex-start" mb={2}>
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
                        <Box
                            bg="bg.muted"
                            color="fg"
                            p={4}
                            rounded="2xl"
                            roundedTopLeft="2px"
                            roundedTopRight="2xl"
                            shadow="none"
                            border="1px solid"
                            borderColor="border"
                        >
                            <Box className="typing-indicator">
                                <Box className="typing-indicator-dot" />
                                <Box className="typing-indicator-dot" />
                                <Box className="typing-indicator-dot" />
                            </Box>
                        </Box>
                    </HStack>
                )}
            </VStack>


            <Box borderTop="1px solid" borderColor="border" p={4}>
                <HStack px={4} py={2}>
                    <Input
                        placeholder="Ask a question about your document..."
                        color="fg"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        size="lg"
                        onKeyDown={handleKeyDown}
                        
                    />
                    <Button
                        aria-label="Send message"
                        size="sm"
                        bg="transparent"
                        color="fg.muted"
                        rounded="full"
                        onClick={handleSendMessage}
                        _hover={{ bg: "bg.emphasized" }}
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