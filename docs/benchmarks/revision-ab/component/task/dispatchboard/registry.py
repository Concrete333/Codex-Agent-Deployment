"""Small tenant configuration registry used by higher-level callers."""


class TenantRegistry:
    def __init__(self, tenants=()):
        self._tenants = set(tenants)

    def require(self, tenant):
        if tenant not in self._tenants:
            raise LookupError(tenant)
        return tenant
