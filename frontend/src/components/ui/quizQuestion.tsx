import { QuizQuestion } from "@/client/types.gen"
import { Box, Text, VStack } from "@chakra-ui/react"
import { useState } from "react"

export default function QuizQuestionComponent({ question }: { question: QuizQuestion }) {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)

  const getOptionStyle = (option: string) => {
    if (!selectedAnswer) return {}
    const isCorrect = option === question.correct_answer
    const isSelected = option === selectedAnswer
    if (isCorrect) {
      return { bg: "bg.success", borderColor: "border.success", color: "fg.success" }
    }
    if (isSelected && !isCorrect) {
      return { bg: "bg.error", borderColor: "border.error", color: "fg.error" }
    }
    return {}
  }

  return (
    <Box
      p={5}
      bg="bg.muted"
      border="1px solid"
      borderColor="border"
      rounded="xl"
      mb={4}
    >
      <Text fontWeight="600" fontSize="md" color="fg" mb={4}>
        {question.question}
      </Text>
      <VStack align="stretch" gap={2}>
        {question.options.map((option, index) => (
          <Box
            onClick={() => !selectedAnswer && setSelectedAnswer(option)}
            border="1px solid"
            borderColor={"border"}
            rounded="lg"
            p={3}
            bg={"bg.panel"}
            _hover={
              !selectedAnswer
                ? { bg: "bg.emphasized", borderColor: "border.emphasized" }
                : {}
            }
            key={index}
            cursor={!selectedAnswer ? "pointer" : "default"}
            transition="all 0.15s"
            {...getOptionStyle(option)}
          >
            <Text fontSize="sm" color="inherit">
              {option}
            </Text>
          </Box>
        ))}
      </VStack>
    </Box>
  )
}
