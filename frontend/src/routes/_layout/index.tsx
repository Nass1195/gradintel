import { createFileRoute } from "@tanstack/react-router"
import UploadBox from "@/components/ui/UploadBox"
import { useState} from "react"
import SummaryResult from "@/components/ui/SummaryResult"
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

  const { data, isLoading, isPlaceholderData } = useQuery({
      ...getItemsQueryOptions(),
      placeholderData: (prevData) => prevData,
  })

  const items = data?.data ?? []


  const [summary, setSummary] = useState<string>("")
  return (<>
    <div style={{ display: "flex", gap: "20px", overflowX: "auto", paddingBottom: "20px", marginBottom: "20px", paddingTop: "20px" }}>
      <AddItem/>
      {isLoading && <div>Loading...</div>}
      {!isLoading && items.map((item) => (
        <ItemCard key={item.id} title={item.title} summarySnippet={item.description || ""} date={item.id} />
      ))
      }
    </div>

    <UploadBox onUploadStart={() => setSummary("aa")} onUploadSuccess={(text) => setSummary(text)}/>
    <SummaryResult content={summary} />
  </>)
}
