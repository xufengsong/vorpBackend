class DebugUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Print the user for every single request that comes in
        print(f"Path: {request.path}, User: {request.user}")
        
        response = self.get_response(request)
        return response