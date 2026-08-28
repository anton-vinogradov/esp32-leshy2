"""Fail-closed 2N7002DW SOT-363 pin/channel invariant for H2 generators."""

from __future__ import annotations


DEVICE_KEY = "diodes_2n7002dw_7_f"
MPN = "Diodes Incorporated 2N7002DW-7-F"
JLCPCB_PART = "C83571"
PIN_MAP = {"1": "S2", "2": "G2", "3": "D1", "4": "S1", "5": "G1", "6": "D2"}


def validate_dual_nmos(
    candidate: dict,
    devices: dict,
    required_instances: set[str] | None = None,
) -> dict:
    """Validate physical pads and every declared channel-to-net assignment."""

    device = devices[DEVICE_KEY]
    actual_pin_map = {
        str(attributes["physical"]): contact
        for contact, attributes in device["contacts"].items()
    }
    if device["mpn"] != MPN or actual_pin_map != PIN_MAP:
        raise ValueError(
            f"exact {MPN} SOT-363 map must be {PIN_MAP}, got {actual_pin_map}"
        )
    if device.get("pinout_invariant", {}).get("physical_pin_to_contact") != PIN_MAP:
        raise ValueError("2N7002DW device pinout invariant disagrees with physical contacts")

    contract = candidate["sot363_2n7002dw_contract"]
    if (
        contract.get("device_key") != DEVICE_KEY
        or contract.get("mpn") != MPN
        or contract.get("jlcpcb_part") != JLCPCB_PART
        or contract.get("physical_pin_to_contact") != PIN_MAP
    ):
        raise ValueError("G2F exact 2N7002DW identity or physical pin map drifted")

    declared_instances = contract["instances"]
    if required_instances is not None and not required_instances <= set(declared_instances):
        missing = sorted(required_instances - set(declared_instances))
        raise ValueError(f"2N7002DW channel contract misses required instances: {missing}")

    route_nets: dict[str, set[str]] = {}
    for route in candidate["fixed_routes"]:
        for endpoint in (route["from"], route["to"]):
            if "." not in endpoint:
                continue
            instance, _ = endpoint.split(".", 1)
            if instance in declared_instances:
                route_nets.setdefault(endpoint, set()).add(route["net"])

    evidence_instances: dict[str, dict] = {}
    for instance, channels in declared_instances.items():
        if candidate["instances"].get(instance) != DEVICE_KEY:
            raise ValueError(f"{instance} is not bound to exact {MPN}")
        channel_contacts: set[str] = set()
        for channel, nets in channels.items():
            suffix = channel.rsplit("_", 1)[-1]
            expected_contacts = {f"G{suffix}", f"S{suffix}", f"D{suffix}"}
            if set(nets) != expected_contacts:
                raise ValueError(
                    f"{instance}.{channel} must declare {sorted(expected_contacts)}, "
                    f"got {sorted(nets)}"
                )
            if channel_contacts & expected_contacts:
                raise ValueError(f"{instance} repeats a 2N7002DW channel terminal")
            channel_contacts.update(expected_contacts)
            for contact, expected_net in nets.items():
                endpoint = f"{instance}.{contact}"
                if route_nets.get(endpoint) != {expected_net}:
                    raise ValueError(
                        f"{endpoint} must connect only to {expected_net}, "
                        f"got {sorted(route_nets.get(endpoint, set()))}"
                    )
        if channel_contacts != set(device["contacts"]):
            raise ValueError(f"{instance} does not account all six 2N7002DW terminals")
        if required_instances is None or instance in required_instances:
            evidence_instances[instance] = channels

    return {
        "device_key": DEVICE_KEY,
        "mpn": MPN,
        "jlcpcb_part": JLCPCB_PART,
        "footprint": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
        "physical_pin_to_contact": PIN_MAP,
        "instances": evidence_instances,
        "source": device["source"],
    }
