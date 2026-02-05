import { QuizQuestion } from "@/client/types.gen"
import QuizQuestionComponent from '@/components/ui/quizQuestion'
import { VStack, Text, Box } from "@chakra-ui/react"

export default function Quizes(quizesQuestions: { quizQuestions: Array<QuizQuestion> }) {
    
    if (!quizesQuestions || quizesQuestions.quizQuestions.length === 0) {
        return (  
            <Box textAlign="center" py={10}>
                <Text>No quiz questions generated yet.</Text>
            </Box>
        )
    }
    
    return (
        <VStack align="stretch" gap={4} w="100%">
            {quizesQuestions.quizQuestions.map((question) => (
                <QuizQuestionComponent  question={question} />
            ))}
        </VStack>
    )
}