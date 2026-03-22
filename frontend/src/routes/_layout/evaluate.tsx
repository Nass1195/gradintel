import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import { fileUploadService } from "@/client"
import { EvaluationPublic } from "@/client/types.gen"
import {
  Button,
  Box,
  VStack,
  Heading,
  Text,
  SimpleGrid,
  Card,
  Flex
} from "@chakra-ui/react"
export const Route = createFileRoute('/_layout/evaluate')({
  component: RouteComponent,
})
const CustomStat = ({ label, value, color = "inherit" }: { label: string, value: string | number, color?: string }) => (
  <Box>
    <Text fontSize="sm" color="gray.500" fontWeight="medium" mb={1}>{label}</Text>
    <Text fontSize="2xl" fontWeight="bold" color={color}>{value}</Text>
  </Box>
);

// Reusable Divider to replace the missing Chakra one
const CustomDivider = () => <Box borderBottomWidth="1px" borderColor="gray.200" my={6} w="full" />;

function RouteComponent() {
  const [status, setStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle');
  const [data, setData] = useState<EvaluationPublic | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');

  const runEvaluation = async () => {
    setErrorMessage('');
    setStatus('running');
    const result = await fileUploadService.runEvaluation()
    setData(result)
    setStatus('completed')
 
  };

 return (
    <Box p={6} maxW="7xl" mx="auto">
      <VStack align="stretch">
        
        <Box mb={4}>
          <Button
            colorScheme="blue"
            onClick={runEvaluation}
            disabled={status === 'running'}
          >
            {status === 'running' ? 'Running Pipeline...' : 'Run Evaluation Pipeline'}
          </Button>
        </Box>

        {status === 'error' && (
          <Box bg="bg.error" color="red.600" p={4} borderRadius="md" borderWidth="1px" borderColor="border.error">
            <Text fontWeight="bold">Error</Text>
            <Text>{errorMessage}</Text>
          </Box>
        )}

        {status === 'completed' && data && (
          <VStack align="stretch" mt={4}>
            
            <Box>
              <Heading size="md" mb={4}>Summary Evaluation (BERT)</Heading>
              <SimpleGrid columns={{ base: 1, md: 3 }} gap={4}>
                {data.summary_evaluation.map((bert, index) => (
                  <Card.Root key={index} variant="outline">
                    <Card.Body>
                      <Text fontWeight="bold" mb={4} color="fg.muted">Summary Chunk #{index + 1}</Text>
                      <Flex justify="space-between" wrap="wrap" gap={4}>
                        <CustomStat label="Precision" value={bert.precision.toFixed(3)} />
                        <CustomStat label="Recall" value={bert.recall.toFixed(3)} />
                        <CustomStat label="F1 Score" value={bert.f1_score.toFixed(3)} color="blue.600" />
                      </Flex>
                    </Card.Body>
                  </Card.Root>
                ))}
              </SimpleGrid>
            </Box>

            <CustomDivider />

            <Box>
              <Heading size="md" mb={4}>RAG Performance</Heading>
              
              <Box mb={6} p={4} bg="bg.panel" borderRadius="md" borderWidth="1px">
                <Text fontWeight="bold" display="inline" mr={2}>Similarity Scores:</Text>
                <Text display="inline" fontFamily="monospace" color="fg.muted">
                  [{data.rag_evaluation.similarity_scores.map(s => s.toFixed(3)).join(', ')}]
                </Text>
              </Box>

              <SimpleGrid columns={{ base: 1, lg: 2 }} gap={4}>
                {data.rag_evaluation.evaluations.map((rag, index) => (
                  <Card.Root key={index} variant="outline" >
                    <Card.Body>
                      <Text fontWeight="bold" mb={4} color="fg.muted">Response Evaluation #{index + 1}</Text>
                      <Flex justify="space-between" wrap="wrap" gap={4} mb={6}>
                        <CustomStat label="Relevance" value={rag.relevance_score.toFixed(1)} />
                        <CustomStat label="Accuracy" value={rag.accuracy_score.toFixed(1)} />
                        <CustomStat label="Completeness" value={rag.completeness_score.toFixed(1)} />
                        <CustomStat label="Overall" value={rag.overall_score.toFixed(1)} color="green.500" />
                      </Flex>
                      <Text fontSize="sm" color="fg.muted"><strong>Explanation:</strong> {rag.explanation}</Text>
                    </Card.Body>
                  </Card.Root>
                ))}
              </SimpleGrid>
            </Box>

            <CustomDivider />

            <Box>
              <Heading size="md" mb={4}>Quiz Question Quality (MCQ)</Heading>
              <SimpleGrid columns={{ base: 1, lg: 2 }} gap={4}>
                {data.quiz_evaluation.map((quiz, index) => (
                  <Card.Root key={index} variant="outline" >
                    <Card.Body>
                      <Text fontWeight="bold" mb={4} color="fg.muted">Question #{index + 1}</Text>
                      <Flex justify="space-between" wrap="wrap" gap={4} mb={6}>
                        <CustomStat label="Accuracy" value={quiz.accuracy_score} />
                        <CustomStat label="Clarity" value={quiz.clarity_score} />
                        <CustomStat label="Distractor" value={quiz.distractor_score} />
                        <CustomStat label="Total" value={quiz.total_score} color="purple.600" />
                      </Flex>
                      <Text fontSize="sm" color="fg.muted"><strong>Reasoning:</strong> {quiz.reasoning}</Text>
                    </Card.Body>
                  </Card.Root>
                ))}
              </SimpleGrid>
            </Box>

          </VStack>
        )}
      </VStack>
    </Box>
  );
}