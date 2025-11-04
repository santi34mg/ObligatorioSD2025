import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
} from "@/components/ui/navigation-menu";

import { useIsMobile } from "@/hooks/use-is-mobile";
import { ProfileMenu } from "./ProfileMenu";

export default function Header() {
  const isMobile = useIsMobile().isMobile;

  return (
    <div className="flex bg-background/80 backdrop-blur-sm border-b border-border px-4 py-2 items-center">
      <NavigationMenu viewport={isMobile} className="py-2 ml-auto">
        <NavigationMenuList className="gap-2 justify-center items-center">
          <NavigationMenuItem>
            <NavigationMenuLink href="/">Home</NavigationMenuLink>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <NavigationMenuLink href="/courses">Courses</NavigationMenuLink>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <NavigationMenuLink href="/connections">
              Connections
            </NavigationMenuLink>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>
      <div className="m-2">
        <ProfileMenu />
      </div>
    </div>
  );
}
