import { Box, Text, HStack, Button, Heading } from "@chakra-ui/react"
import { FaCopy} from "react-icons/fa"
import { toaster } from "@/components/ui/toaster"
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

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
        h = "100%"
        border="1px solid" 
        borderColor="gray.200"
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
        <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]} >
          {!content || content.trim() === "" ? "No summary available." : content}
        </ReactMarkdown >
      </Box>
    </Box>
  )
}