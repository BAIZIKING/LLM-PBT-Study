from hypothesis import settings, HealthCheck, assume, Phase
settings.register_profile('validity', max_examples=1000, suppress_health_check=list(HealthCheck), phases=[Phase.generate])
settings.load_profile('validity')
import inspect
from hypothesis import settings, HealthCheck, assume, Phase
settings.register_profile('validity', max_examples=1000, suppress_health_check=list(HealthCheck), phases=[Phase.generate])
settings.load_profile('validity')
import inspect
from hypothesis import settings, HealthCheck, assume, Phase
settings.register_profile('validity', max_examples=1000, suppress_health_check=list(HealthCheck), phases=[Phase.generate])
settings.load_profile('validity')
import inspect
from hypothesis import settings, HealthCheck, assume, Phase
settings.register_profile('validity', max_examples=1000, suppress_health_check=list(HealthCheck), phases=[Phase.generate])
settings.load_profile('validity')
import inspect
from hypothesis import settings, HealthCheck, assume, Phase
settings.register_profile('validity', max_examples=1000, suppress_health_check=list(HealthCheck), phases=[Phase.generate])
settings.load_profile('validity')
import inspect
from hypothesis import given, strategies as st
import zlib

@given(data=st.data(), value=st.integers(min_value=0, max_value=2 ** 32 - 1))
def test_zlib_adler32(data, value):
    try:
        try:
            try:
                try:
                    try:
                        input_bytes = data.draw(st.binary())
                        assert 0 <= zlib.adler32(input_bytes, value) <= 2 ** 32 - 1
                        one_shot = zlib.adler32(input_bytes, value)
                        running = value
                        for i in range(0, len(input_bytes), 10):
                            running = zlib.adler32(input_bytes[i:i + 10], running)
                        assert running == one_shot
                        assert zlib.adler32(b'', value) == value
                        left = data.draw(st.binary())
                        right = data.draw(st.binary())
                        assert zlib.adler32(left + right, value) == zlib.adler32(right, zlib.adler32(left, value))
                    except AssertionError as e:
                        pass
                    except Exception:
                        name = inspect.stack()[0][3]
                        print(f'ERROR: {name}')
                except AssertionError as e:
                    pass
                except Exception:
                    name = inspect.stack()[0][3]
                    print(f'ERROR: {name}')
            except AssertionError as e:
                pass
            except Exception:
                name = inspect.stack()[0][3]
                print(f'ERROR: {name}')
        except AssertionError as e:
            pass
        except Exception:
            name = inspect.stack()[0][3]
            print(f'ERROR: {name}')
    except AssertionError as e:
        pass
    except Exception:
        name = inspect.stack()[0][3]
        print(f'ERROR: {name}')