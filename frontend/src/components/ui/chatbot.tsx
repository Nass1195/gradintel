import { Box, Button, Flex, Heading, HStack, Input, Text, VStack } from "@chakra-ui/react";
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
        <Flex direction="column" h="100%" overflow="hidden" >
            <VStack align="stretch" flex="1" overflowY="auto" p={4} gap={6}>
                <Heading as="h2" size="xl" mb={2}>
                    AI Chatbot
                </Heading>
                {messages.map((msg, index) => (
                    <HStack key={index} maxW="100%" align="start"  justifyContent={msg.role === 'user' ? 'flex-end' : 'flex-start'} mb={2}>
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
                            bg="white"
                            color="gray.800"
                            p={4}
                            rounded="2xl"
                            roundedTopLeft="2px"
                            roundedTopRight="2xl"
                            shadow="sm"
                            border="1px solid"
                            borderColor="gray.200"
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