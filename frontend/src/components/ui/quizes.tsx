import { QuizQuestion } from "@/client/types.gen"
import QuizQuestionComponent from '@/components/ui/quizQuestion'
import { VStack, Text, Box, Button, Flex, IconButton } from "@chakra-ui/react"
import { fileUploadService } from "@/client"
import { useState } from "react";
import { IoRefreshOutline, IoFilterOutline } from "react-icons/io5";

type QuizesProps = {
    selectedFile: File | null;
};

export default function Quizes({selectedFile }: QuizesProps) {
    const [quiz, setQuiz] = useState<Array<QuizQuestion>>([])
    const [isLoading, setIsLoading] = useState<boolean>(false)
    
    const handleQuizGeneration = async () => {
        if (!selectedFile) {
            console.log("No file selected for quiz generation.")
            return
        }
        setIsLoading(true)
        try {
            console.log("Generating quiz questions for file:", selectedFile.name)
            const respond = await fileUploadService.uploadFileForQuiz(selectedFile)
            const quizes = respond.questions
            setQuiz(quizes)
            setIsLoading(false)
        } catch (error) {
            console.error("Error generating quiz questions:", error)
        }    
    }    
    if (!quiz || quiz.length === 0) {
        return ( 
            <VStack>
                <Box textAlign="center" py={10}>
                    <Text>No quiz questions generated yet.</Text>
                </Box>
                <Button onClick={handleQuizGeneration} loading={isLoading}>
                    Please upload a file to generate quiz questions.
                </Button>
            </VStack>
                
        )
    }
    
    return (
        <VStack align="stretch" gap={4} w="100%">
            <Flex align="center" justify="space-between">
                <Text fontSize="sm" fontWeight="bold" letterSpacing="wider">
                    PRACTICE QUIZ
                </Text>
                <IconButton
                    aria-label="Refresh Quiz"
                    size="lg"
                    bg="transparent"
                    _hover={{bg: "white", color: "black"}}
                    rounded="md"
                    color="white"
                    loading={isLoading}
                    onClick={handleQuizGeneration}   
                >
                    <IoRefreshOutline/>
                </IconButton>
            </Flex>
            <VStack align="stretch" gap={4} w="100%">
                {quiz.map((question) => (
                    <QuizQuestionComponent  question={question} />
                ))}
            </VStack>
        </VStack>
        
    )
}