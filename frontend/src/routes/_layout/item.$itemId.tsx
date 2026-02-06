import { createFileRoute } from '@tanstack/react-router'
import  UploadBox  from '@/components/ui/UploadBox'
import SummaryResult from "@/components/ui/SummaryResult"
import { Box, Tabs } from '@chakra-ui/react'
import Quizes from '@/components/ui/quizes'
import { FaRobot, FaQuestionCircle } from 'react-icons/fa'
import { DocumentPublic } from '@/client/types.gen'
import { fileUploadService } from '@/client'


import { useEffect, useState } from 'react'

export const Route = createFileRoute('/_layout/item/$itemId')({
  component: RouteComponent,
})

function RouteComponent() {
  const itemId = Route.useParams().itemId
  const [file, setFile] = useState<File | null>(null)
  const [summary, setSummary] = useState<string>(" ")
  const [document, setDocument] = useState<DocumentPublic | null>(null)

  useEffect(() => {
    const fetchFile = async () => {
      try {
        const response = await fileUploadService.getFile(itemId)
        const summary = response.summary || "No summary available."
        setSummary(summary)
        setDocument(response)
      } catch (error) {
        console.error("Error fetching file summary:", error)
        setSummary("Failed to load summary.")
      }
    } 
    fetchFile()
  }, [itemId])
  
  return (
    <div style={{ display: "flex", flexDirection: "row", gap: "20px", paddingBottom: "20px", marginBottom: "20px", paddingTop: "20px", height: "100%" }}>
      <Box w={{ base: '100%', lg: '35%' }} minW="350px" overflowY="auto" pr={2}>
        <UploadBox
          onUploadStart={(selectedFile) => {
            setSummary("")
            setFile(selectedFile)
          }}
          onUploadSuccess={(text) => setSummary(text)}
          itemId={itemId}
          document={document}
        />
        <Box mt={6}>
          <SummaryResult content={summary} />
        </Box>
      </Box>

      <Box w={{ base: '100%', lg: '65%' }} rounded="2xl" shadow="sm" border="1px solid" borderColor="gray.200" overflow="hidden" display="flex" flexDirection="column">
        <Tabs.Root defaultValue="chat" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box borderBottom="1px solid" borderColor="gray.200" px={4} pt={4}>
            <Tabs.List gap={4}>
              <Tabs.Trigger value="chat"
                px={4} py={2}
                _selected={{ borderBottomWidth: "2px" }}
                fontWeight="medium"
                style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
              >
               <FaRobot /> AI Chat
              </Tabs.Trigger>
              <Tabs.Trigger value="quiz"
                px={4} py={2}
                _selected={{  borderBottomWidth: "2px" }}
                
                fontWeight="medium"
                style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <FaQuestionCircle /> Quiz Mode
              </Tabs.Trigger>
            </Tabs.List>
          </Box>

          <Tabs.Content value="chat" p={0} flex="1" overflow="hidden">
              
          </Tabs.Content>
          <Tabs.Content value="quiz" p={6} flex="1" overflowY="auto">
            <Quizes selectedFile={file} />
          </Tabs.Content>
        </Tabs.Root>
      </Box>
    </div>
    
  )
}
