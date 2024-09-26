from enum import Enum


class OrderStatusEnum(str, Enum):
    in_process = "in_process"
    sent = "sent"
    delivered = "delivered"

    # Маппинг для отображения статусов на русском языке
    @property
    def label(self):
        labels = {
            "in_process": "в процессе",
            "sent": "отправлен",
            "delivered": "доставлен"
        }
        return labels[self.value]
