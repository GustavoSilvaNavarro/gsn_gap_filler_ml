from fastapi import APIRouter, Response, status

router = APIRouter()


@router.get(
    "/healthz",
    tags=["Monitoring"],
    description="Health check endpoint",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def healthz() -> Response:
    """Check the condition of the server to ensure it is running.

    Returns:
        Response: A response with status code 204 indicating the server is healthy.
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)
