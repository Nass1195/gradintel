
import { Box, Icon, Text, Button, VStack, Input, HStack } from "@chakra-ui/react"
import { useState, ChangeEvent } from "react"
import { fileUploadService } from "@/client"
import { toaster } from "@/components/ui/toaster"
import { QuizQuestion } from "@/client/types.gen"
import { FaCloudUploadAlt, FaFilePdf, FaTrash } from "react-icons/fa"
import { count } from "console"

interface UploadFileProps {
    onUploadStart: () => void;           
    onUploadSuccess: (summary: string) => void; 
    onUploadQuizSuccess: (quizes: Array<QuizQuestion>) => void;
}

export default function UploadBox({ onUploadStart, onUploadSuccess, onUploadQuizSuccess }: UploadFileProps) {
    const [file, setFile] = useState<File | null>(null)
    const [isUploading, setIsUploading] = useState(false)

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files?.[0]
        if (selected){
            setFile(selected)
            handleUpload(selected)
        }
    }

    const handleUpload = async (selectedFile: File) => {
        if (!selectedFile) {
            toaster.create({
                title: "No file selected",
                description: "Please select a file to upload.",
                type: "error",
                duration: 3000,
            })
            return
        }

        onUploadStart()
        setIsUploading(true)


        try {
            const respond = await fileUploadService.uploadFile(selectedFile)
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
            setIsUploading(false)
        } finally {
            setIsUploading(false)
        }
    }

    const handleUploadQuiz = async () => {
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
        setIsUploading(true)


        try {
            const respond = await fileUploadService.uploadFileForQuiz(file)
            const quizes = respond.questions
            onUploadQuizSuccess(quizes)
    
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
            setIsUploading(false)
        } finally {
            setIsUploading(false)
        }
    }

    const handleRemoveFile = () => {
        setFile(null)
        onUploadStart()
    }

    return (
        
        <Box 
            border="1px solid " 
            p={6} 
            rounded="2xl"
            shadow="sm"
            h="fit-content"
        >
            <HStack mb={4} gap={2}>
                <Icon as={FaCloudUploadAlt} color="blue.500" boxSize={5} />
                <Text fontSize="lg" fontWeight="bold">
                    Upload your document
                </Text>
            </HStack>

            {!file ? (
                <Box
                    border="2px dashed"
                    rounded="xl"
                    p={8}
                    textAlign="center"
                    cursor="pointer"
                    position="relative"
                >
                    <Input 
                        type="file"
                        onChange={handleFileChange}
                        position="absolute"
                        top={0}
                        left={0}
                        w="100%"
                        h="100%"
                        opacity={0}
                        cursor="pointer"
                    />
                    <VStack gap={3}>
                        <Icon as={FaCloudUploadAlt} boxSize={6} />
                        <VStack gap={0}>
                            <Text fontWeight="semibold" >Click to upload or drag and drop</Text>
                            <Text fontSize="sm" >PDF, DOCX, or TXT</Text>
                        </VStack>
                    </VStack>
                </Box>
            ) : (
                <Box
                    border="1px solid"
                    rounded="xl"
                    p={4}
                >
                    <HStack justify="space-between">
                        <HStack gap={3}>
                            <Box
                                bg="red.100"
                                p={2}
                                rounded="lg"
                                display="flex"
                                alignItems="center"
                                justifyContent="center"
                            >
                                <Icon as={FaFilePdf} boxSize={5} color="red.500" />
                            </Box>
                            <VStack align="start" gap={0}>
                                <Text fontWeight="medium" >{file.name}</Text>
                                <Text fontSize="xs">{(file.size / 1024 / 1024).toFixed(1)} MB • {isUploading ? "Processing..." : "Uploaded just now"}</Text>
                            </VStack>
                        </HStack>
                        <Button
                            onClick={handleRemoveFile}
                            bg="transparent"
                        >
                            <FaTrash />
                        </Button>
                    </HStack>
                </Box>

            )}
            
            
        </Box>
  
    )
}
