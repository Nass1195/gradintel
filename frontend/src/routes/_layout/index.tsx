import {  Flex, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { ItemCard } from "@/components/ui/DashboardCards"
import { ItemsService } from "@/client"
import { useQuery } from "@tanstack/react-query"
import  AddItem  from "@/components/Items/AddItem"



export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function getItemsQueryOptions() {
  return {
    queryFn: () =>
      ItemsService.readItems(),
    queryKey: ["items"],
  }
}


function Dashboard() {

  const { data, isLoading } = useQuery({
      ...getItemsQueryOptions(),
      placeholderData: (prevData) => prevData,
  })

  const items = data?.data ?? []


  return (
    <Flex w="100%" gap={4} flexWrap="wrap">
      <AddItem  />
      {isLoading && (
        <Text fontSize="sm" color="gray.500">
          Loading items...
        </Text>
      )}
      {!isLoading && items.map((item) => (
        <ItemCard
          item={item}
          
        />
      ))}
     
    </Flex>
  )
}
