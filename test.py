
async def test(a, b):
    print("H")

fname = test("1", "2").__qualname__

# Get the argument values
frame = test("1", "2").cr_frame
args = frame.f_locals  # dict object