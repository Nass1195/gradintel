
import { Box, Container, Text, Button, VStack, Input } from "@chakra-ui/react"
import { useState, ChangeEvent } from "react"
import { fileUploadService } from "@/client"
import { toaster } from "@/components/ui/toaster"

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
        toaster.create({
            title: "No file selected",
            description: "Please select a file to upload.",
            type: "error",
            duration: 3000,
        })
        return
        }

        onUploadStart()
        setIsLoading(true)


        try {
            const respond = await fileUploadService.uploadFile(file)
            const summary = respond.message
            onUploadSuccess(summary)
    
            toaster.create({
                title: "File uploaded successfully",
                description: "The file has been summarized.",
                type: "success",
                duration: 3000,
            })
        } catch (error) {
            toaster.create({
                title: "Upload failed",
                description: "There was an error uploading the file.",
                type: "error",
                duration: 3000,
            })
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
