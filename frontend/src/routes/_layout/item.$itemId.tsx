import { createFileRoute } from '@tanstack/react-router'
import UploadBox from '@/components/ui/UploadBox'
import SummaryResult from "@/components/ui/SummaryResult"
import Chatbot from "@/components/ui/chatbot"
import { Box, Tabs, Flex, Stack } from '@chakra-ui/react'
import Quizes from '@/components/ui/quizes'
import { FaRobot, FaQuestionCircle } from 'react-icons/fa'
import { DocumentPublic } from '@/client/types.gen'
import { fileUploadService, ItemsService } from '@/client'


import { useEffect, useState } from 'react'

export const Route = createFileRoute('/_layout/item/$itemId')({
  component: RouteComponent,
})

function RouteComponent() {
  const itemId = Route.useParams().itemId
  const [summary, setSummary] = useState<string>("")
  const [documents, setDocument] = useState<Array<DocumentPublic>>([])

  useEffect(() => {
    const fetchFile = async () => {
      try {
        const item = await ItemsService.readItem(itemId)
        setSummary(item.summary ? item.summary : "No summary available.")
        const response = await fileUploadService.getFile(itemId)
        setDocument(response.data)
      } catch (error) {
        console.error("Error fetching file summary:", error)
      }
    }
    fetchFile()
  }, [itemId])
  
  return (
    <Flex
      direction={{ base: 'column', lg: 'row' }}
      gap={6}
      py={6}
      h="100%"
    >
      <Stack w={{ base: '100%', lg: '35%' }} minW={{ lg: '320px' }}>
        <UploadBox
          onUploadStart={(doc, summary) => {
            setDocument(doc)
            setSummary(summary)
          }}
          onUploadSuccess={(savedDocuments, summary) => {
            setDocument(savedDocuments)
            setSummary(summary)
          }}
          onDeleteFile={(summary) => {
            setSummary(summary)
          }}
          itemId={itemId}
          document={documents}
        />
        <SummaryResult content={summary} />
      </Stack>

      <Box
        w={{ base: '100%', lg: '65%' }}
        rounded="2xl"
        bg="bg.panel"
        border="1px solid"
        borderColor="border"
        overflow="hidden"
        display="flex"
        flexDirection="column"
      >
        <Tabs.Root defaultValue="chat" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box borderBottom="1px solid" borderColor="border" px={4} pt={4}>
            <Tabs.List gap={4}>
              <Tabs.Trigger
                value="chat"
                px={4}
                py={2}
                _selected={{ borderBottomWidth: "2px", borderColor: "border.emphasized" }}
                fontWeight="medium"
                style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
              >
               <FaRobot /> AI Chat
              </Tabs.Trigger>
              <Tabs.Trigger
                value="quiz"
                px={4}
                py={2}
                _selected={{ borderBottomWidth: "2px", borderColor: "border.emphasized" }}
                fontWeight="medium"
                style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <FaQuestionCircle /> Quiz Mode
              </Tabs.Trigger>
            </Tabs.List>
          </Box>

          <Tabs.Content value="chat" p={0} flex="1" overflow="hidden">
              <Chatbot itemId={itemId}/>
          </Tabs.Content>
          <Tabs.Content value="quiz" p={6} flex="1" overflowY="auto">
            <Quizes itemId={itemId}/>
          </Tabs.Content>
        </Tabs.Root>
      </Box>
    </Flex>
    
  )
}
