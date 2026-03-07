import { Box, Text, VStack, Icon, Heading, HStack } from "@chakra-ui/react"
import { FiFileText } from "react-icons/fi" // Make sure to install react-icons or use chakra icons
import DeleteItem from "@/components/Items/DeleteItem"
import EditItem from "@/components/Items/EditItem"
import type { ItemPublic } from "@/client"
import { Link } from "@tanstack/react-router"



interface ItemCardProps {
  item: ItemPublic
}

export const ItemCard = ({ item }: ItemCardProps) => {
  return (
    <Box
      h="200px"
      minW="350px"
      borderRadius="lg"
      border="1px solid"
      borderColor="border"
      bg="bg.panel"
      shadow="none"
      position="relative"
      transition="all 0.2s"
      _hover={{ shadow: "sm", transform: "translateY(-2px)", borderColor: "border.emphasized" }}
      cursor="pointer"
      display="flex"
      flexDirection="column"
    >
      <Link
        key={item.id}
        to="/item/$itemId"
        params={{ itemId: item.id }}
        search={{ page: 1 }}
        style={{ height: "100%"}}
      >
        <VStack align="start" gap={3} flex={1} p={5}>
          <Box display="flex" alignItems="center" gap={2} w="100%">
            <Icon as={FiFileText} color="fg.info" />
            <Heading size="sm" >{item.title}</Heading>
          </Box>
          
          <Text fontSize="sm" >
            {item.description}
          </Text>
        </VStack>
      </Link>

      <HStack gap={2} p={3} justify="flex-end" >
        <EditItem item={item} /> 
        <DeleteItem id={item.id} />
      </HStack>

     
    </Box>
  )
}