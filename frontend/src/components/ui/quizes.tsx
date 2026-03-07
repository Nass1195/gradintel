import { QuizQuestion } from "@/client/types.gen"
import QuizQuestionComponent from "@/components/ui/quizQuestion"
import { VStack, Text, Box, Button, Flex, IconButton } from "@chakra-ui/react"
import { fileUploadService } from "@/client"
import { useState } from "react"
import { IoRefreshOutline } from "react-icons/io5"

type QuizesProps = {
  itemId: string
}

export default function Quizes({ itemId }: QuizesProps) {
  const [quiz, setQuiz] = useState<Array<QuizQuestion>>([])
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const handleQuizGeneration = async () => {
    setIsLoading(true)
    try {
      const respond = await fileUploadService.uploadFileForQuiz(itemId)
      const quizes = respond.questions
      setQuiz(quizes)
    } catch (error) {
      console.error("Error generating quiz questions:", error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!quiz || quiz.length === 0) {
    return (
      <VStack align="stretch" gap={4} py={8}>
        <Box textAlign="center" py={6}>
          <Text fontSize="sm" color="fg.muted">
            No quiz questions yet. Generate a set to practice.
          </Text>
        </Box>
        <Button
          onClick={handleQuizGeneration}
          loading={isLoading}
          variant="outline"
          borderColor="border"
          _hover={{ bg: "bg.emphasized"}}
          color="fg"
          size="sm"
        >
          Generate quiz questions
        </Button>
      </VStack>
    )
  }

  return (
    <VStack align="stretch" gap={4} w="100%">
      <Flex align="center" justify="space-between">
        <Text fontSize="" fontWeight="600" color="fg.muted" letterSpacing="wider">
          Practice quiz
        </Text>
        <IconButton
          aria-label="Refresh quiz"
          size="sm"
          bg="transparent"
          _hover={{bg: "bg.emphasized"}}
          color="fg.muted"
          loading={isLoading}
          onClick={handleQuizGeneration}
        >
          <IoRefreshOutline />
        </IconButton>
      </Flex>
      <VStack align="stretch" gap={4} w="100%">
        {quiz.map((q, i) => (
          <QuizQuestionComponent key={i} question={q} />
        ))}
      </VStack>
    </VStack>
  )
}