from finance.models import Investment

class ROIService:

    @staticmethod
    def process_due_investments():

        ...

    @staticmethod
    def process_investment(investment):

        ...

    @staticmethod
    def complete_investment(investment):

        ...


def process_all_investments():

    processed = 0

    investments = Investment.objects.filter(
        status="active"
    )

    for investment in investments:

        processed += 1

        # ROI logic will come here

    return processed