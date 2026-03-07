import { Box, HStack, Button, Heading } from "@chakra-ui/react"
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
    <Box w="100%" pt={6} pb={6} minH="80%">
      <Box 
        p={5} 
        rounded="2xl" 
        h = "100%"
        border="1px solid" 
        borderColor="border"
        overflowY="auto"
        bg="bg.panel"
        shadow="none"

      >

        <HStack justify="space-between" mb={4}>
          <HStack gap={2}>
            <Heading size="md">Summary</Heading>
          </HStack>
          <Button
            aria-label="Copy summary"
            bg="transparent"
            color="fg.muted"
            _hover={{ bg: "bg.emphasized" }}
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