import { Flex, Image, useBreakpointValue, Box, Text } from "@chakra-ui/react"
import { Link } from "@tanstack/react-router"

import Logo from "/assets/images/logo.png"
import UserMenu from "./UserMenu"

function Navbar() {
  const display = useBreakpointValue({ base: "none", md: "flex" })

  return (
    <Flex
      display={display}
      justify="space-between"
      position="sticky"
      color="white"
      align="center"
      bg="white"
      _dark={{ bg: "gray.800", color: "white" }}
      w="100%"
      top={0}
      p={4}
    >
      <Link to="/">
        <Flex align="center" gap={1}>
          <Image src={Logo} alt="Logo" maxW="70px" />
          <Box>
            <Text fontSize="sm" fontWeight="semibold" color="fg">
              Study Assist
            </Text>
          </Box>
        </Flex>
      </Link>
      <Flex gap={2} alignItems="center">
        <UserMenu />
      </Flex>
    </Flex>
  )
}

export default Navbar
