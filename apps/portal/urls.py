from django.urls import path
from .views import (
    PortalDashboardView,
    PortalProductDetailView,
    PortalProductChallengeFilterView,
    PortalProductBountiesView,
    PortalProductBountyFilterView,
    PortalReviewWorkView,
    PortalContributorAgreementTemplateListView,
    PortalManageBountiesView,
    PortalBountyClaimRequestsView,
    PortalManageUsersView,
    PortalAddProductUserView,
    PortalUpdateProductUserView,
    PortalProductSettingView,
    DeleteBountyClaimView,
    PortalProductChallengesView,
    bounty_claim_actions,
)

app_name = 'portal'

urlpatterns = [
    path("", PortalDashboardView.as_view(), name="home"),
    path(
        "product/<str:product_slug>/<int:default_tab>/",
        PortalDashboardView.as_view(),
        name="product-dashboard",
    ),
    path(
        "bounties/",
        PortalManageBountiesView.as_view(),
        name="manage-bounties",
    ),
    path(
        "bounties/bounty-requests",
        PortalBountyClaimRequestsView.as_view(),
        name="bounty-requests",
    ),
    path(
        "product/<str:product_slug>/tab/<int:default_tab>/",
        PortalProductDetailView.as_view(),
        name="product-detail",
    ),
    path(
        "product/<str:product_slug>/challenges/",
        PortalProductChallengesView.as_view(),
        name="dashboard-product-challenges",
    ),
    path(
        "product/<str:product_slug>/challenges/filter/",
        PortalProductChallengeFilterView.as_view(),
        name="product-challenge-filter",
    ),
    path(
        "product/<str:product_slug>/bounties/",
        PortalProductBountiesView.as_view(),
        name="product-bounties",
    ),
    path(
        "bounties/action/<int:pk>/",
        bounty_claim_actions,
        name="bounties-action",
    ),
    path(
        "product/<str:product_slug>/bounties/filter/",
        PortalProductBountyFilterView.as_view(),
        name="product-bounty-filter",
    ),
    path(
        "product/<str:product_slug>/review-work",
        PortalReviewWorkView.as_view(),
        name="review-work",
    ),
    path(
        "product/<str:product_slug>/contributor-agreement-templates",
        PortalContributorAgreementTemplateListView.as_view(),
        name="contributor-agreement-templates",
    ),
    path(
        "product/<str:product_slug>/user-management",
        PortalManageUsersView.as_view(),
        name="manage-users",
    ),
    path(
        "product/<str:product_slug>/add-product-user",
        PortalAddProductUserView.as_view(),
        name="add-product-user",
    ),
    path(
        "product/<str:product_slug>/product-users/<int:pk>/update",
        PortalUpdateProductUserView.as_view(),
        name="update-product-user",
    ),
    path(
        "product/<str:product_slug>/settings/",
        PortalProductSettingView.as_view(),
        name="product-settings",
    ),
    path(
        "bounty-claim/delete/<int:pk>",
        DeleteBountyClaimView.as_view(),
        name="delete-bounty-claim",
    ),
]
