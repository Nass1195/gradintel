import { Box, Text, } from "@chakra-ui/react"

interface SummaryResultProps {
  content: string;
}

export default function SummaryResult({ content }: SummaryResultProps) {
  

  // If there is no content, don't render anything
  if (!content) return null

  return (
    <Box w="100%"  style={{ paddingTop: "50px", paddingBottom: "50px", minHeight: "100%"}} animation="fadeIn 0.5s">
      

      <Box 
        p={5} 
        rounded="md" 
        h = "100%"
        border="1px solid" 
        borderColor="gray.200"
        maxH="400px"
        overflowY="auto"
        shadow="inner"

      >
        <Text >
          {content}
        </Text>
      </Box>
    </Box>
  )
}