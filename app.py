from shiny import App, render, ui
import boto3
import os

# UI layout
app_ui = ui.page_fluid(
    ui.input_text("queue_name", "Enter SQS Queue Name", placeholder="Queue Name"),
    ui.input_text("account_id", "Enter AWS Account ID", placeholder="Account ID"),
    ui.tags.div(
        ui.output_text_verbatim("queue_info_output"),
        style="white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word;",
    ),
    ui.tags.div(  # Section for displaying the ARN
        ui.output_text_verbatim("queue_arn_output"),
        style="white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word;",
    ),
    ui.tags.div(  # New section for displaying server responses
        ui.output_text_verbatim("server_response_output"),
        style="white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word; color: red;",
    ),
)


# Server logic
def server(input, output, session):
    @output
    @render.text
    def queue_info_output():
        queue_name = input.queue_name()
        account_id = input.account_id()
        if queue_name:  # Check if the queue name input is not empty
            queue_info = get_sqs_queue_info(queue_name, account_id)
            return queue_info.get("url", "Queue URL not available.")
        else:
            return "Please enter a queue name."

    @output
    @render.text
    def queue_arn_output():
        queue_name = input.queue_name()
        account_id = input.account_id()
        if queue_name:
            queue_info = get_sqs_queue_info(queue_name, account_id)
            return queue_info.get("arn", "Queue ARN not available.")
        else:
            return "Waiting for ARN to be displayed..."

    @output
    @render.text
    def server_response_output():
        queue_name = input.queue_name()
        account_id = input.account_id()
        if queue_name:
            queue_info = get_sqs_queue_info(queue_name, account_id)
            if "error" in queue_info:
                return queue_info["error"]
            else:
                return "Queue information retrieved successfully."
        else:
            return "No response"


def get_sqs_queue_info(queue_name, account_id):
    # Initialize an SQS service resource
    account_id = account_id
    os.environ["AWS_REGION"] = "us-east-2"
    sqs = boto3.resource("sqs", region_name="us-east-2")
    try:
        # Attempt to get the queue by name
        queue = sqs.get_queue_by_name(
            QueueName=queue_name,
            QueueOwnerAWSAccountId=account_id,
        )
        # If successful, return both the queue URL and ARN
        queue_info = {"url": f"Queue URL: {queue.url}", "arn": f"Queue ARN: {queue.attributes['QueueArn']}"}
        return queue_info
    except Exception as e:
        # If there's an error, return a message indicating failure
        return {"error": f"Failed SQS queue: {e}"}


app = App(app_ui, server)
