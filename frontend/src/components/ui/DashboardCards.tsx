import { Box, Text, VStack, Icon, Heading, Badge } from "@chakra-ui/react"
import { FiFileText, FiClock } from "react-icons/fi" // Make sure to install react-icons or use chakra icons


interface ItemCardProps {
  title: string;
  summarySnippet: string;
  date: string;
}

export const ItemCard = ({ title, summarySnippet, date }: ItemCardProps) => {
  return (
    <Box
      h="200px"
      w="100%"
      border="1px solid"
      borderColor="gray.200"
      rounded="xl"
      p={5}
      shadow="sm"
      position="relative"
      transition="all 0.2s"
      _hover={{ shadow: "md", transform: "translateY(-2px)" }}
      cursor="pointer"
      display="flex"
      flexDirection="column"
    >
      <VStack align="start" gap={3} flex={1}>
        <Box display="flex" alignItems="center" gap={2} w="100%">
          <Icon as={FiFileText} color="blue.500" />
          <Heading size="sm" >{title}</Heading>
        </Box>
        
        <Text fontSize="sm" >
          {summarySnippet}
        </Text>
      </VStack>

      <Box mt="auto" pt={4} display="flex" justifyContent="space-between" alignItems="center">
        <Badge colorScheme="blue" fontSize="xs">Processed</Badge>
        <Box display="flex" alignItems="center" gap={1} color="gray.400">
           <Icon as={FiClock} boxSize={3} />
           <Text fontSize="xs">{date}</Text>
        </Box>
      </Box>
    </Box>
  )
}