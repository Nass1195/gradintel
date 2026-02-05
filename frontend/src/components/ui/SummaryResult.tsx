import { Box, Text, HStack, Button, Heading } from "@chakra-ui/react"
import { FaCopy} from "react-icons/fa"

interface SummaryResultProps {
  content: string;
}

export default function SummaryResult({ content }: SummaryResultProps) {
  

  // If there is no content, don't render anything
  if (!content  || content.trim() === "") return null

  return (
    <Box w="100%"  style={{ paddingTop: "50px", paddingBottom: "50px", minHeight: "80%"}} animation="fadeIn 0.5s">
      

      <Box 
        p={5} 
        rounded="2xl" 
        h = "fit-content"
        border="1px solid" 
        borderColor="gray.200"
        maxH="400px"
        overflowY="auto"
        shadow="inner"

      >

        <HStack justify="space-between" mb={4}>
          <HStack gap={2}>
            <Heading size="md">Summary</Heading>
          </HStack>
          <Button
            aria-label="Copy summary"
            variant="ghost"
            color="gray.400"
            size="sm"
          >
            <FaCopy />
          </Button>
        </HStack>
        <Text >
          {content}
        </Text>
      </Box>
    </Box>
  )
}