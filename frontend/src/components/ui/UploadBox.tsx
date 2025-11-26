
import { Box, Container, Text, Button, VStack, Input } from "@chakra-ui/react"
import { useState, ChangeEvent } from "react"
import { fileUploadService } from "@/client"

export default function UploadBox() {
  const [file, setFile] = useState<File | null>(null)

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0]
    if (selected) setFile(selected)
  }

  const handleUpload = () => {
    if (!file) {
      alert("No file selected")
      return
    }


    fileUploadService.uploadFile(file).then((message) => {
      console.log(message)
      setFile(null)
    })
    
    alert("File uploaded successfully!")
  }

  return (
    <Container maxW="lg" pt={12}>
      <VStack gap={6} border="1px solid #ddd" p={6} rounded="xl">
        <Text fontSize="2xl" fontWeight="bold">
          Upload File
        </Text>

        <Box
          border="2px dashed #bbb"
          p={10}
          rounded="lg"
          textAlign="center"
          w="100%"
        >
          <Text mb={4}>Drag & drop your file here</Text>
          <Input type="file" onChange={handleFileChange} cursor="pointer" border="none" />
        </Box>

        <Button colorScheme="blue" w="100%" onClick={handleUpload}>
          Upload
        </Button>
      </VStack>
    </Container>
  )
}
