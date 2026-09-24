import { loadQuartzConfig, loadQuartzLayout } from "./quartz/plugins/loader/config-loader"
import { componentRegistry } from "./quartz/components/registry"
import SchemaOrg from "./quartz/components/SchemaOrg"

// Register custom components
componentRegistry.register("SchemaOrg", SchemaOrg, "local")

const config = await loadQuartzConfig()
export default config
export const layout = await loadQuartzLayout()
