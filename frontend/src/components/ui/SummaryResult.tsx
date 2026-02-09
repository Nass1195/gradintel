import { Box, Text, HStack, Button, Heading } from "@chakra-ui/react"
import { FaCopy} from "react-icons/fa"
import { toaster } from "@/components/ui/toaster"

interface SummaryResultProps {
  content: string | null | undefined;
}

export default function SummaryResult({ content }: SummaryResultProps) {

  const handelCopySummary = async () => {
    if (!content) {
      return
    }
    await navigator.clipboard.writeText(content)
    toaster.create({
      title: "Summary copied to clipboard",
      type: "success",
      duration: 3000,
    })
  }
  

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
            onClick={handelCopySummary}
          >
            <FaCopy />
          </Button>
        </HStack>
        <Text >
          {!content || content.trim() === "" ? "No summary available." : content}
        </Text>
      </Box>
    </Box>
  )
}