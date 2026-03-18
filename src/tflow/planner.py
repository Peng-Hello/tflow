from typing import Dict, Any, List

def generate_test_plan(analysis: Dict[str, Any]) -> str:
    """Generate a markdown test plan based on project analysis."""
    lines = ["# E2E Test Plan\n"]
    
    auth_flows = analysis.get("auth_flows", [])
    if auth_flows:
        lines.append("## P0: Authentication Flows")
        for idx, flow in enumerate(auth_flows):
            lines.append(f"### Test {idx+1}: {flow.get('name', 'Login')}")
            lines.append(f"- Pattern: AUTH_FLOW")
            lines.append(f"- Description: {flow.get('description', '')}")
            lines.append("")
            
    routes = analysis.get("routes", [])
    if routes:
        lines.append("## P1: Core Navigation & CRUD")
        for idx, route in enumerate(routes):
            lines.append(f"### Test Route {route.get('path', '/')}")
            lines.append(f"- Pattern: ROUTE_LOAD")
            lines.append(f"- Component: {route.get('component', 'Unknown')}")
            lines.append("")
            
    return "\n".join(lines)

def parse_test_plan(plan_markdown: str) -> List[Dict[str, Any]]:
    """Parse editable markdown test plan back into structural data."""
    # Stub
    return []
