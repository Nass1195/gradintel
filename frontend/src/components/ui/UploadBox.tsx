
import { Box, Container, Text, Button, VStack, Input } from "@chakra-ui/react"
import { useState, ChangeEvent } from "react"
import { fileUploadService } from "@/client"

interface UploadFileProps {
  onUploadStart: () => void;           
  onUploadSuccess: (summary: string) => void; 
}

export default function UploadBox({ onUploadStart, onUploadSuccess }: UploadFileProps) {
    const [file, setFile] = useState<File | null>(null)
    const [isLoading, setIsLoading] = useState(false)

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files?.[0]
        if (selected) setFile(selected)
    }

    const handleUpload = async () => {
        if (!file) {
        alert("No file selected")
        return
        }

        onUploadStart()
        setIsLoading(true)


        try {
            const respond = await fileUploadService.uploadFile(file)
            const summary = respond.message
            onUploadSuccess(summary)
    
            alert("File uploaded successfully!")
        } catch (error) {
            console.error("Upload failed:", error)
            alert("File upload failed. Please try again.")
            setIsLoading(false)
        } finally {
            setIsLoading(false)
        }
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

            <Button 
                colorScheme="blue" 
                w="100%" 
                onClick={handleUpload}
                loading={isLoading}
                loadingText="Summarizing..."
                disabled={!file}
            >
                Upload & Summarize
            </Button>
        </VStack>
        </Container>
    )
}
