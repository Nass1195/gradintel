import { createFileRoute } from '@tanstack/react-router'
import { useEffect, useState } from 'react'
import { fileUploadService } from "@/client"
import { EvaluationPublic,  BertEvaluation, RAGEvaluation} from "@/client/types.gen"
import {
  Button,
  Box,
  VStack,
  Heading,
  Text,
  SimpleGrid,
  Card,
  Flex,
  Dialog
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

interface ActiveChunk extends BertEvaluation {
  index: number;
}

interface ActiveRagChunk extends RAGEvaluation {
  index: number;
  similarity_score?: number; 
}

// Reusable Divider to replace the missing Chakra one
const CustomDivider = () => <Box borderBottomWidth="1px" borderColor="gray.200" my={6} w="full" />;

function RouteComponent() {
  const [status, setStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle');
  const [data, setData] = useState<EvaluationPublic | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [activeChunk, setActiveChunk] = useState<ActiveChunk | null>(null);
  const [activeRagChunk, setActiveRagChunk] = useState<ActiveRagChunk | null>(null);
  const [isRagModalOpen, setIsRagModalOpen] = useState<boolean>(false);

  const handleOpenModal = (chunkData: BertEvaluation, index: number) => {
    setActiveChunk({ ...chunkData, index });
    setIsModalOpen(true);
  };
  
  const handleCloseModal = (): void => {
    setIsModalOpen(false);
    setActiveChunk(null);
  };

  const handleOpenRagModal = (ragData: RAGEvaluation, index: number, similarity: number): void => {
    setActiveRagChunk({ ...ragData, index, similarity_score: similarity });
    setIsRagModalOpen(true);
  };

  const handleCloseRagModal = (): void => {
    setIsRagModalOpen(false);
    setActiveRagChunk(null);
  };

  useEffect(() => {
      const fetchEvaluation= async () => {
        try {
          const response = await fileUploadService.getEvaluation()
          setData(response)
          setStatus('completed')
        } catch (error) {
          console.error("Error fetching Evaluation:", error)
        }
      }
      fetchEvaluation()
  }, [])

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
                      <Text fontWeight="bold" mb={4} color="blue.600" cursor="pointer" _hover={{ textDecoration: "underline", color: "blue.700" }}  onClick={() => handleOpenModal(bert, index)}>Summary Chunk #{index + 1}</Text>
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


            <Dialog.Root 
              open={isModalOpen} 
              onOpenChange={(e) => {
                
                if (!e.open) handleCloseModal();
              }} 
              size="xl"
            >
              <Dialog.Backdrop />
              <Dialog.Positioner>
                <Dialog.Content>
                  <Dialog.Header>
                    <Dialog.Title>
                      Summary Chunk #{activeChunk !== null ? activeChunk.index + 1 : ''}
                    </Dialog.Title>
                  </Dialog.Header>
                  <Dialog.CloseTrigger />
                  
                  <Dialog.Body pb={6}>
                    <Text fontSize="sm" fontWeight="bold" mb={2} color="fg.subtle" textTransform="uppercase">
                      Original Text
                    </Text>
                    <Box p={4} bg="gray.50" borderWidth="1px" borderColor="border.subtle" borderRadius="md" mb={6}>
                      <Text fontSize="sm" color="fg.default">
                        {activeChunk?.original_text}
                      </Text>
                    </Box>

                    <Text fontSize="sm" fontWeight="bold" mb={2} color="fg.subtle" textTransform="uppercase">
                      Generated Summary
                    </Text>
                    <Box p={4} bg="blue.50" borderWidth="1px" borderColor="blue.100" borderRadius="md">
                      <Text fontSize="sm" color="gray.800">
                        {activeChunk?.summary}
                      </Text>
                    </Box>
                  </Dialog.Body>
                </Dialog.Content>
              </Dialog.Positioner>
            </Dialog.Root>

            <CustomDivider />

            <Box>
              <Heading size="md" mb={4}>RAG Performance</Heading>
              
              <SimpleGrid columns={{ base: 1, lg: 2 }} gap={4}>
                {data.rag_evaluation.evaluations.map((rag, index) => (
                  <Card.Root key={index} variant="outline">
                    <Card.Body>
                      <Text fontWeight="bold" mb={4} color="blue.600" cursor="pointer" _hover={{ textDecoration: "underline", color: "blue.700" }} onClick={() => handleOpenRagModal(rag, index, data.rag_evaluation.similarity_scores?.[index])}>Response Evaluation #{index + 1}</Text>
                      
                      <Flex justify="space-between" wrap="wrap" gap={4} mb={6}>
                        
                        <CustomStat 
                          label="Similarity" 
                          value={data.rag_evaluation.similarity_scores?.[index]?.toFixed(3) ?? "N/A"} 
                          color="blue.500" 
                        />
                        
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

            <Dialog.Root 
              open={isRagModalOpen} 
              onOpenChange={(e) => {
                if (!e.open) handleCloseRagModal();
              }} 
              size="xl"
            >
              <Dialog.Backdrop />
              <Dialog.Positioner>
                <Dialog.Content>
                  <Dialog.Header>
                    <Dialog.Title>
                      Response Evaluation #{activeRagChunk !== null ? activeRagChunk.index + 1 : ''}
                    </Dialog.Title>
                  </Dialog.Header>
                  <Dialog.CloseTrigger />
                  
                  <Dialog.Body pb={6}>
                    {/* The Question */}
                    <Box mb={6}>
                      <Text fontSize="xs" fontWeight="bold" color="fg.muted" textTransform="uppercase" tracking="wider">
                        User Query
                      </Text>
                      <Text fontWeight="semibold" fontSize="md" mt={1} color="fg.default">
                        {activeRagChunk?.user_query}
                      </Text>
                    </Box>
                    
                    {/* The Answers Side-by-Side */}
                    <SimpleGrid columns={{ base: 1, md: 2 }} gap={4}>
                      {/* Generated Answer */}
                      <Box p={3} borderWidth="1px" borderRadius="md" bg="blue.50" borderColor="blue.100">
                        <Text fontSize="xs" fontWeight="bold" color="blue.600" textTransform="uppercase" mb={2}>
                          ✨ Generated Answer
                        </Text>
                        <Text fontSize="sm" color="gray.800">
                          {activeRagChunk?.generated_answer}
                        </Text>
                      </Box>

                      {/* Real Answer */}
                      <Box p={3} borderWidth="1px" borderRadius="md" bg="green.50" borderColor="green.100">
                        <Text fontSize="xs" fontWeight="bold" color="green.600" textTransform="uppercase" mb={2}>
                          🎯 Ground Truth
                        </Text>
                        <Text fontSize="sm" color="gray.800">
                          {activeRagChunk?.ground_truth}
                        </Text>
                      </Box>
                    </SimpleGrid>
                  </Dialog.Body>
                </Dialog.Content>
              </Dialog.Positioner>
            </Dialog.Root>

            <CustomDivider />

            <Box>
              <Heading size="md" mb={4}>Quiz Question Quality (MCQ)</Heading>
              <SimpleGrid columns={{ base: 1, lg: 2 }} gap={4}>
                {data.quiz_evaluation.map((quiz, index) => (
                  <Card.Root key={index} variant="outline" >
                    <Card.Body>
                      <Text fontWeight="bold" mb={4} color="fg.muted">Question #{index + 1}</Text>
                      <Box mb={6} pb={6} borderBottomWidth="1px" borderColor="border.subtle">
        
                       
                        <Box mb={5} p={4} bg="gray.50" borderRadius="md" borderWidth="1px" borderColor="gray.200">
                          <Text fontSize="xs" fontWeight="bold" color="gray.500" textTransform="uppercase" mb={2} >
                            📄 Source Text Context
                          </Text>
                         
                          <Text fontSize="sm" color="gray.700">
                            {quiz.source_text}
                          </Text>
                        </Box>

                        
                        <Box mb={4}>
                          <Text fontSize="xs" fontWeight="bold" color="blue.600" textTransform="uppercase" mb={1}>
                            ✨ Generated Question
                          </Text>
                          <Text fontWeight="semibold" fontSize="lg" color="fg.default">
                            {quiz.question}
                          </Text>
                        </Box>

                        
                        <Box>
                          <Text fontSize="xs" fontWeight="bold" color="gray.500" textTransform="uppercase" mb={2}>
                            Options
                          </Text>
                          <Flex direction="column" gap={2}>
                            
                            {quiz.options.map((option, optIndex) => (
                              <Box 
                                key={optIndex} 
                                p={2} 
                                px={3} 
                                borderWidth="1px" 
                                borderRadius="md" 
                                bg="white"
                                borderColor="gray.200"
                              >
                                <Text fontSize="sm" color="gray.800">
                                  
                                  {option}
                                </Text>
                              </Box>
                            ))}
                          </Flex>
                        </Box>

                      </Box>
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