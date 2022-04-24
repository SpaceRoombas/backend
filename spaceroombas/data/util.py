import random
from threading import Timer


def create_interpreter_function_bindings(game_state, bot):
    up = (lambda args: game_state.move_robot_up(bot.owner, bot.robot_id), 0)
    down = (lambda args: game_state.move_robot_down(bot.owner, bot.robot_id), 0)
    left = (lambda args: game_state.move_robot_left(bot.owner, bot.robot_id), 0)
    right = (lambda args: game_state.move_robot_right(
        bot.owner, bot.robot_id), 0)
    move = (lambda args: [up, right, down, left][args[0][0]][0]([]), 1)
    terraform = (lambda args: bot.terraform(game_state), 0)
    mine = (lambda args: bot.mine(game_state, args[0][0]), 1)
    look = (lambda args: bot.look(game_state, args[0][0]), 1)
    reproduce = (lambda args: bot.reproduce(game_state, args[0][0]), 1)
    resources = (lambda args: bot.resources, 0)
    rand_dir = (lambda args: random.randrange(0, 4), 0)

    fns = {"move_north": up, "move_south": down, "move_west": left, "move_east": right, "terraform": terraform,
           "mine": mine, "look": look, "reproduce": reproduce, "resources": resources, "rand_dir": rand_dir,
           "move": move}

    return fns


def debounce(secs):
    """
    Function decorator which acts similar to debounce function in Lodash

    When the decorated function is called, it will be delayed by `secs` seconds.
    Successive calls cancel previous calls.
    """

    def decorator(fn):
        def d(*args, **kwargs):
            def call_fn():
                d._timer = None
                return fn(*args, **kwargs)

            if d._timer is not None:
                d._timer.cancel()

            d._timer = Timer(secs, call_fn)
            d._timer.start()

        d._timer = None
        return d

    return decorator
