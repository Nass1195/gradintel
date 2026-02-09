
import { Box, Icon, Text, Button, VStack, Input, HStack } from "@chakra-ui/react"
import { useState, ChangeEvent, useEffect } from "react"
import { fileUploadService } from "@/client"
import { toaster } from "@/components/ui/toaster"
import { FaCloudUploadAlt, FaFilePdf, FaTrash } from "react-icons/fa"
import { DocumentPublic } from '@/client/types.gen'


interface UploadFileProps {
    onUploadStart: (doc: Array<DocumentPublic>) => void;           
    onUploadSuccess: (document: Array<DocumentPublic>) => void;
    itemId: string
    document: Array<DocumentPublic> 
}

export default function UploadBox({ onUploadStart, onUploadSuccess, itemId, document }: UploadFileProps) {
    const [savedDocument, setSavedDocument] = useState<Array<DocumentPublic>>([])

    useEffect(() => {
        if (document) {
            setSavedDocument(document)
        }
    }, [document])

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files?.[0]
        if (selected){
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

        const doc: DocumentPublic = {
            id: "",
            title: selectedFile.name,
            summary: "generating summary...",
        }
        const newDocuments = [...savedDocument]
        newDocuments.push(doc)
        setSavedDocument(newDocuments)
        onUploadStart(newDocuments)


        try {
            const respond = await fileUploadService.uploadFile(itemId,selectedFile)
            const document = respond
            const newDocuments = [...savedDocument]
            newDocuments.push(document)
            setSavedDocument(newDocuments)
            onUploadSuccess(newDocuments)
    
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
        } finally {
        }
    }

    const handleRemoveFile = (index: number) => {
        const document = savedDocument[index]
        const newDocuments = savedDocument.filter((_, i) => i !== index)
        setSavedDocument(newDocuments)
        onUploadStart(newDocuments)
        if (document?.id) {
            fileUploadService.deleteFile(document?.id).catch(() => {
                toaster.create({
                    title: "Delete failed",
                    description: "There was an error deleting the file.",
                    type: "error",
                    duration: 3000,
                })
            })
        }
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

            <Box>
                <Box
                    border="2px dashed"
                    rounded="xl"
                    p={8}
                    textAlign="center"
                    cursor="pointer"
                    position="relative"
                    mb={4}
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
                {savedDocument.map((doc, index) => (
                    <Box
                        border="1px solid"
                        rounded="xl"
                        p={4}
                        mb={3}
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
                                    <Text fontWeight="medium" >{doc.title}</Text>
                                    <Text fontSize="sm">{doc.id == "" ? "Processing..." : "Uploaded just now"} </Text>
                                </VStack>
                            </HStack>
                            <Button
                                onClick={() => handleRemoveFile(index)}
                                bg="transparent"
                            >
                                <FaTrash />
                            </Button>
                        </HStack>
                    </Box>
                ))}

            </Box>

           
           
            
            
        </Box>
  
    )
}
