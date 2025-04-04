class SecurityQuestionHandler:
    def __init__(self):
        self.next = None

    def set_next(self, handler):
        self.next = handler
        return handler

    def handle(self, user_input, expected_answer):
        raise NotImplementedError("Must override handle method")


class Question1Handler(SecurityQuestionHandler):
    def handle(self, user_input, expected_answer):
        if user_input != expected_answer:
            return False
        if self.next:
            return self.next.handle_chain()
        return True

    def handle_chain(self):
        return self.next.handle_chain() if self.next else True


class Question2Handler(SecurityQuestionHandler):
    def handle(self, user_input, expected_answer):
        if user_input != expected_answer:
            return False
        if self.next:
            return self.next.handle_chain()
        return True

    def handle_chain(self):
        return self.next.handle_chain() if self.next else True


class Question3Handler(SecurityQuestionHandler):
    def handle(self, user_input, expected_answer):
        return user_input == expected_answer

    def handle_chain(self):
        return True  # End of chain


class PasswordRecoveryManager:
    def __init__(self):
        self.q1 = Question1Handler()
        self.q2 = Question2Handler()
        self.q3 = Question3Handler()
        self.q1.set_next(self.q2).set_next(self.q3)

    def recover_password(self, inputs, expected):
        return (self.q1.handle(inputs[0], expected[0]) and
                self.q2.handle(inputs[1], expected[1]) and
                self.q3.handle(inputs[2], expected[2]))
