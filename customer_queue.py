from linkedlist import LinkedList
from collections import deque
from time import gmtime, time
import uuid


class Customer(object):
    def __init__(self, name, party_num, present = False, uid=None):
        self.name = name
        self.party_num = party_num
        self.present = present
        self.enqueue_time = time()
        self.uid = uid if uid else uuid.uuid1()


class CustomerQueueLL(LinkedList):
    def __init__(self):
        super().__init__()

    def find_by_uid(self, uid):
        return self.find(lambda x: x.uid == uid)

    def delete_by_uid(self, uid):
        return self.delete_q(lambda x: x.uid == uid)

    def find_by_uid_and_update(self, uid, item):
        return self.update_append(lambda x: x.uid == uid, item)

    def find_next_eligible(self):
        return self.find(lambda x: x.present == True)


# class CustomerQueueDeque(deque):


def test_customer_queue():
    test_party_1 = Customer('Fang', 1)
    test_party_2 = Customer('Fang', 2)
    test_party_3 = Customer('Fang', 3)
    customer_queue = CustomerQueueLL()
    customer_queue.append(test_party_1)
    customer_queue.append(test_party_2)
    customer_queue.append(test_party_3)
    print('find', customer_queue.find_by_uid(test_party_3.uid))
    print('find', customer_queue.find_by_uid('abc'))
    print('iterator', customer_queue.iter)
    # customer_queue.delete_q(lambda x: x.uid == test_party_2.uid)
    customer_queue.delete_by_uid(test_party_2.uid)
    print('iterator', customer_queue.iter)
    print(customer_queue)
    print(customer_queue.head.data.name)
    for i in customer_queue:
        print(i.data.name, i.data.party_num, i.data.uid)
    return customer_queue


if __name__ == '__main__':
    print(test_customer_queue())
