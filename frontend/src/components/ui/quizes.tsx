import { QuizQuestion } from "@/client/types.gen"
import QuizQuestionComponent from "@/components/ui/quizQuestion"
import { VStack, Text, Box, Button, Flex, IconButton, Heading, ProgressCircle, AbsoluteCenter } from "@chakra-ui/react"
import { fileUploadService } from "@/client"
import { useEffect, useState } from "react"
import { IoRefreshOutline } from "react-icons/io5"

type QuizesProps = {
  itemId: string
}

export default function Quizes({ itemId }: QuizesProps) {
  const [quiz, setQuiz] = useState<Array<QuizQuestion>>([])
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [answeredQuestions, setAnsweredQuestions] = useState<number>(0)
  const [correctAnswers, setCorrectAnswers] = useState<number>(0)

  useEffect(() => {
    const fetchChatLogs = async () => {
      try {
        const response = await fileUploadService.getQuiz(itemId)
        setQuiz(response.questions)
      } catch (error) {
        console.error("Error fetching chat logs:", error)
      }
    }
    fetchChatLogs()
  }, [itemId])

  const handleQuizGeneration = async () => {
    setIsLoading(true)
    try {
      const respond = await fileUploadService.generateQuiz(itemId)
      const quizes = respond.questions
      setQuiz(quizes)
      setAnsweredQuestions(0)
      setCorrectAnswers(0)
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

  if (!quiz || answeredQuestions == quiz.length) {
    const percentage = answeredQuestions > 0 
      ? Math.round((correctAnswers / answeredQuestions) * 100) 
      : 0;

    let feedbackMessage = "Keep practicing!";
    let ringColor = "red";
    if (percentage >= 80) {
      feedbackMessage = "Outstanding!"
      ringColor = "green";
    } else if (percentage >= 50) {
      feedbackMessage = "Good job!"
      ringColor = "orange";
    }

    return (
      <VStack
        justify="center"
        align="center"
        gap={6}
        p={8}
        bg="bg.muted"
        borderRadius="xl"
        boxShadow="lg"
        mt={10}
      >
        <VStack gap={1}>
          <Heading size="xl" color="fg">Quiz Complete!</Heading>
          <Text fontSize="lg" color="fg">{feedbackMessage}</Text>
        </VStack>
        <ProgressCircle.Root value={percentage} colorPalette={ringColor} boxSize="auto"  justifyContent={"center"}>
          <ProgressCircle.Circle css={{ "--thickness": "18px", "--size": "150px" }}>
            <ProgressCircle.Track/>
            <ProgressCircle.Range/>
          </ProgressCircle.Circle>
          <AbsoluteCenter>
            <VStack gap={1}>
              <Text fontSize="4xl" fontWeight="extrabold" color="fg.muted">
                {correctAnswers}
              </Text>
              <Text fontSize="md" color="fg.muted" fontWeight="medium">
                out of {answeredQuestions}
              </Text>
            </VStack>
          </AbsoluteCenter>
        </ProgressCircle.Root>
        <Text fontSize="2xl" fontWeight="bold" color="fg.muted">
          Score: {percentage}%
        </Text>
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
        {quiz.map((q) => (
          <QuizQuestionComponent 
            key={q.question} 
            question={q} 
            onQuizAnswer={(iscorrect) => {
              setAnsweredQuestions(answeredQuestions + 1)
              if (iscorrect) setCorrectAnswers(correctAnswers + 1)
            }}
          />
        ))}
      </VStack>
    </VStack>
  )
}