"""Read-only reporting over the supplied storage adapter."""


def event_count_by_tenant(store, tenants):
    return {tenant: len(store.all_for(tenant)) for tenant in tenants}
