import { createFileRoute } from "@tanstack/react-router"
import UploadBox from "@/components/ui/UploadBox"
import SummaryResult from "@/components/ui/SummaryResult"



export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})


function Dashboard() {
  return (<>
    <UploadBox />
    <SummaryResult content="This is a sample summary result displayed after file upload." />
  </>)
}
