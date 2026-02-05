import { QuizQuestion } from "@/client/types.gen"
import { Box, Text, VStack } from "@chakra-ui/react";
import { useState } from "react";


export default function QuizQuestionComponent( {question} : { question: QuizQuestion }) {
    const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);

    const getBorderColor = (option: string) => {
        if (option === question.correct_answer) {
            return "green";
        }
        return "red";
    };

 
    
    return(
        <Box p={6} border="1px solid" borderColor="gray.200" rounded="xl" shadow="sm"  mb={4}>
            <Text fontWeight="bold" fontSize="lg" mb={4}>
                {question.question}
            </Text>
            <VStack align="stretch" gap={3}>
                {question.options.map((option, index) => (
                    <Box 
                        onClick={() => !selectedAnswer && setSelectedAnswer(option)} 
                        border="2px solid"
                        rounded="lg"
                        p={3}
                        _hover={!selectedAnswer  ? {bg: "grey"} : {}}
                        borderColor={selectedAnswer ? getBorderColor(option) : "gray.200"}
                        key={index}
                        cursor={!selectedAnswer ? "pointer" : "default"}
                        transition="all 0.2s"
                        position="relative"
                    >
                        <Text >
                            {option}
                        </Text>
                    </Box>
                ))}
            </VStack>
        </Box>
    )
}
